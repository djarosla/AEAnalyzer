from glob import glob
import uproot3
import numpy as np
import pandas as pd
import tqdm
from RooPandasFunctions import PNanotoDataFrame,PSequential,PColumn,PFilter,PRow,PProcessor,PProcRunner,PInitDir
from collections import OrderedDict

#Define Datasets and corresponding file selections
fnames={}
fnames["QCD_HT1000to1500"] = sorted(glob('/cms/knash/EOS/QCD_HT1000to1500_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8/RunIISummer20UL16MiniAOD-106X_mcRun2_asymptotic_v13-v1_NanoB2GNano2016mc_v1/*/*/*.root'))
fnames["QCD_HT1500to2000"]= sorted(glob('/cms/knash/EOS/QCD_HT1500to2000_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8/RunIISummer20UL16MiniAOD-106X_mcRun2_asymptotic_v13-v1_NanoB2GNano2016mc_v1/*/*/*.root'))
fnames["QCD_HT2000toInf"]= sorted(glob('/cms/knash/EOS/QCD_HT2000toInf_TuneCP5_PSWeights_13TeV-madgraphMLM-pythia8/RunIISummer20UL16MiniAOD-106X_mcRun2_asymptotic_v13-v1_NanoB2GNano2016mc_v1/*/*/*.root'))
fnames["TT"] = sorted(glob('/cms/knash/EOS/ZprimeToTT_M2500_W25_TuneCP2_PSweights_13TeV-madgraph-pythiaMLM-pythia8/RunIISummer20UL16MiniAOD-106X_mcRun2_asymptotic_v13-v2_NanoB2GNano2016mc_v1/*/*/*.root'))
#fnames["WgWg"] = sorted(glob('/cms/knash/EOS/SQSQtoqchiqchitoWs_M1500_M400_M200/knash-RunIISummer20UL16MiniAOD-106X_mcRun2_asymptotic_v13-76761e5076679f48cfaad96c1b8156aa_NanoB2GNano2016mc_v1/*/*/*.root'))


#Do this if accessing over XROOTD
fileset={}
for ffi in fnames:
    #fileset[ffi]=[ffj.replace("/eos/uscms/","root://cmsxrootd.fnal.gov///") for ffj in fnames[ffi]]
    fileset[ffi]=fnames[ffi]
    #fileset[ffi]=fileset[ffi][:10]

#This is the Nano->Parquet file reduction factor
batchesperfile={"TT":3,"QCD_HT1500to2000":5,"QCD_HT1000to1500":5,"QCD_HT2000toInf":5} #"WgWg":1

#Keep only the branches you want "Jet",["pt"] would be the branch Jet_pt in the NanoAOD
branchestokeep=OrderedDict([("Muon",["pt","eta","phi","mass"]),("Jet",["pt","eta","phi","mass"]),("FatJet",["pt","eta","phi","mass","msoftdrop","iAEMSE","iAEL0","iAEL1","iAEL2","iAEL3","iAEL4","iAEL5"]),("",["run","luminosityBlock","event","PV_npvs","PV_npvsGood","fixedGridRhoFastjetAll"])])

#Trim out element indices you dont want (ie only keep top 5 jets etc)
mind={"FatJet":5,"Jet":5,"Muon":5,"":None}


#It is possible to pass a column selection here similar to the analyzer.  
#Clearly the syntax is overly complicated compared to the analyzer -- to improve.  
#This is useful for skimming and calculating a value from collections that you dont want to save.
#ex/calculate ht from ak4 jets, then drop ak4s:
class ColumnSelection():
    def __call__(self,df,EventInfo):

            htdf=pd.DataFrame()
            htdf["ht"]=df["Jet_pt"].groupby(level=0).sum()
            htdf['subentry'] = 0
            htdf.set_index('subentry', append=True, inplace=True)
            df=pd.concat((df,htdf),axis=1)

            df=df.drop(["Jet_pt","Jet_eta","Jet_phi","Jet_mass"],axis=1)

            return df
         
skim=  [
        PColumn(ColumnSelection()),
       ]

#Run it.  nproc is the number of processors.  >1 goes into multiprocessing model
PNanotoDataFrame(fileset,branchestokeep,filesperchunk=batchesperfile,nproc=1,atype="flat",dirname="RooFlatFull",maxind=mind,seq=skim).Run()

